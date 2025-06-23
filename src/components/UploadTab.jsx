import React, { useState } from 'react';
import { Upload, CheckCircle, AlertCircle, Video } from 'lucide-react';

const UploadTab = () => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [podcaster, setPodcaster] = useState('andrew_huberman');
  const [platforms, setPlatforms] = useState(['tiktok', 'instagram']);
  const [uploadResult, setUploadResult] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileInput = async (e) => {
    if (e.target.files && e.target.files[0]) {
      await handleFiles(e.target.files);
    }
  };

  const handleFiles = async (files) => {
    const file = files[0];
    if (!file.type.startsWith('audio/') && !file.type.startsWith('video/')) {
      alert('Please select an audio or video file');
      return;
    }

    setUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('podcaster', podcaster);
      platforms.forEach(platform => formData.append('platforms', platform));

      const response = await fetch('http://localhost:8000/upload/analyze', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadResult(result);
        console.log('Upload successful:', result);
      } else {
        const error = await response.json();
        alert(`Upload failed: ${error.detail}`);
      }
    } catch (error) {
      alert(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handlePlatformChange = (platform) => {
    setPlatforms(prev => 
      prev.includes(platform)
        ? prev.filter(p => p !== platform)
        : [...prev, platform]
    );
  };

  return (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-semibold mb-4">Upload Audio for Analysis</h2>
        
        {/* Configuration */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium mb-2">Podcaster</label>
            <select
              value={podcaster}
              onChange={(e) => setPodcaster(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white"
              disabled={uploading}
            >
              <option value="andrew_huberman">Andrew Huberman</option>
              <option value="joe_rogan">Joe Rogan</option>
              <option value="chris_williamson">Chris Williamson</option>
              <option value="unknown">Other</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Target Platforms</label>
            <div className="flex flex-wrap gap-3">
              {['tiktok', 'instagram', 'youtube_shorts'].map(platform => (
                <label key={platform} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={platforms.includes(platform)}
                    onChange={() => handlePlatformChange(platform)}
                    className="mr-2"
                    disabled={uploading}
                  />
                  <span className="text-sm capitalize">
                    {platform.replace('_', ' ')}
                  </span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Upload Area */}
        <div
          className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
            dragActive
              ? 'border-purple-500 bg-purple-500/10'
              : 'border-gray-600 hover:border-gray-500'
          } ${uploading ? 'opacity-50' : 'cursor-pointer'}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {uploading ? (
            <div className="flex flex-col items-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mb-4"></div>
              <p className="text-lg">Processing your audio...</p>
              <p className="text-sm text-gray-400 mt-2">This may take a few minutes</p>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <Upload className="h-12 w-12 text-gray-400 mb-4" />
              <p className="text-lg mb-2">Drop your audio file here, or click to browse</p>
              <p className="text-sm text-gray-400 mb-4">Supports MP3, WAV, M4A, MP4 up to 100MB</p>
              <input
                type="file"
                accept="audio/*,video/*"
                onChange={handleFileInput}
                className="hidden"
                id="file-upload"
                disabled={uploading}
              />
              <label
                htmlFor="file-upload"
                className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-md cursor-pointer transition-colors"
              >
                Browse Files
              </label>
            </div>
          )}
        </div>
      </div>

      {/* Results */}
      {uploadResult && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center mb-4">
            <CheckCircle className="h-6 w-6 text-green-500 mr-2" />
            <h3 className="text-lg font-semibold">Analysis Complete!</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-2xl font-bold text-purple-400">
                {uploadResult.clips_found}
              </div>
              <div className="text-sm text-gray-400">Clips Detected</div>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-2xl font-bold text-blue-400">
                {platforms.length}
              </div>
              <div className="text-sm text-gray-400">Target Platforms</div>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-2xl font-bold text-green-400">
                {uploadResult.success ? 'Success' : 'Failed'}
              </div>
              <div className="text-sm text-gray-400">Status</div>
            </div>
          </div>

          {/* Clips List */}
          {uploadResult.clips && uploadResult.clips.length > 0 && (
            <div className="space-y-4">
              <h4 className="font-semibold">Detected Clips:</h4>
              {uploadResult.clips.map((clip, index) => (
                <div key={index} className="bg-gray-700 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h5 className="font-medium">Clip {index + 1}</h5>
                    <span className="bg-purple-600 text-white px-2 py-1 rounded text-xs">
                      Score: {(clip.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <p className="text-sm text-gray-300 mb-2">
                    {clip.start_time.toFixed(1)}s - {clip.end_time.toFixed(1)}s 
                    ({clip.duration.toFixed(1)}s duration)
                  </p>
                  <p className="text-sm text-gray-400 mb-2">
                    {clip.transcript.substring(0, 150)}...
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {clip.keywords && clip.keywords.map((keyword, i) => (
                      <span key={i} className="bg-gray-600 text-xs px-2 py-1 rounded">
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UploadTab;
