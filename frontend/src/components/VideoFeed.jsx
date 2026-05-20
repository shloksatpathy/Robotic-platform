function VideoFeed({ frame }) {

  return (
    <div className="video-feed">

      <h3>Live Video Feed</h3>

      {frame ? (
        <img
          src={`data:image/jpeg;base64,${frame}`}
          alt="Live Feed"
          className="video-stream"
        />
      ) : (
        <div className="video-placeholder">
          Waiting for stream...
        </div>
      )}

    </div>
  );
}

export default VideoFeed;