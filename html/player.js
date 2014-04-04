/*!
 * jQuery music player JSON communications
 *
 * Copyright 2014 Liam Wickins
 *
 * Depends:
 *	jquery.ajax
 */
(function ( $ ) {

  var url = "http://localhost:8000",
  track = [],
  playlist = [],
  powerOn = false,
  consoleLoggingOn = false,
  volume = null,
  lastVolume = null,
  shuffle = null,
  lastShuffle = null,
  sinks = [],
  lastSinks = [],
  curSink = 0,
  trackState = null,
  lastTrackState = null,
  playlistHash = null,
  lastPlaylistHash = null,
  imageCache = {},
  refreshPeriod = 5000,
  callbacks = {};

  var getItem = function(resp, item, def) {
    val = def || null;
    $.each(resp, function() {
      $.each(this, function(k, v) {
        if (k == item) {
          val = v;
          return false; // Terminate 'each' here, item found
        }
        return true;
      });
    });
    return val;
  };

  var debugLog = function(msg) {
    if (consoleLoggingOn) {
      console.log(msg);
    }
  };

  var musicCommand = function(cmd, callback) {
    var data = JSON.stringify({'command':cmd});
    $.ajax({ type:'POST', url:url, data:data, async:true,
             contentType:'application/json',
             dataType:'json', success:callback });
  };

  var updateStats = function() {
    musicCommand('stats', function(data) {
      if (player.EVENT_TRACK_POSITION in callbacks) {
        var cb = callbacks[player.EVENT_TRACK_POSITION];
        vals = calcTrackPosition(data);
        cb(vals[0], vals[1]);
      }
    });
  };

  var notifyPlaylist = function() {
    var pos;
    if (track) {
      pos = getItem(track, 'playlistPosition');
    } else {
      pos = null; // No track will be highlighted in playlist
    }
    if (player.EVENT_PLAYLIST in callbacks) {
      var cb = callbacks[player.EVENT_PLAYLIST];
      cb(playlist, pos, imageCache);
    }
  };

  var getTrackImage = function(trackUri, param, callback) {
    if (trackUri in imageCache) {
      // Image is cached, so notify with data from cache
      callback(false,
               param,
               imageCache[trackUri]);
    } else {
      musicCommand('image ' + trackUri, function(data) {
        imageCache[trackUri] = getItem(data,'albumImage');
        callback(true,
                 param,
                 imageCache[trackUri]);
      });
    }
  };

  var loadPlaylistImages = function() {
    for (var i = 0; i < playlist.length; i++) {
      uri = playlist[i]['link'];
      getTrackImage(uri, i, function(isNew, idx, image) {
        if (isNew && player.EVENT_PLAYLIST in callbacks) {
          notifyPlaylist();
        }
      });
    }
  };

  var notifyCurrentTrackImage = function(state, trackUri) {
    if (player.EVENT_TRACK_IMAGE in callbacks) {
      var cb = callbacks[player.EVENT_TRACK_IMAGE];
      cb(null); // Clear current image while new one loads
      if (trackUri && (state == 'playing' || state == 'paused')) {
        getTrackImage(trackUri, null, function(isNew, param, img) {
          var cb = callbacks[player.EVENT_TRACK_IMAGE];
          cb(img);
        });
      }
    }
  };

  var notifyTrackInfo = function(state, tr) {
    if (player.EVENT_TRACK_INFO in callbacks) {
      var cb = callbacks[player.EVENT_TRACK_INFO];
      if (state == 'playing' || state == 'paused') {
        cb(tr);
        notifyPlaylist(); // Allow current playlist highlight to update
      } else {
        cb(null); // Use this to clear current track information
      }
    }
  };

  var notifyPlayState = function(state) {
    if (player.EVENT_PLAY_STATE in callbacks) {
      var cb = callbacks[player.EVENT_PLAY_STATE];
      if (state == 'playing') {
        cb(true);
      } else {
        cb(false);
      }
    }
  };
 
  var updateTrack = function() {
    musicCommand('info track', function(data) {
      track = data;
      var t = getItem(track, 'track');
      var state = getTrackPlayState();
      var trackUri = getTrackUri();
      trackState = trackUri + "-" + state;
      if (lastTrackState != trackState) {
        notifyTrackInfo(state, t);
        notifyPlayState(state);
        notifyCurrentTrackImage(state, trackUri);
      }
      lastTrackState = trackState;
    });
  };

  var updatePlaylist = function() {
    musicCommand('info playlisthash', function(data) {
      playlistHash = getItem(data, 'playlisthash');
      if (playlistHash != lastPlaylistHash) {
        musicCommand('info playlist', function(data) {
          playlist = getItem(data, 'playlist');
          notifyPlaylist();
          loadPlaylistImages();
        });
      }
      lastPlaylistHash = playlistHash;
    });
  };

  var notifyVolume = function() {
    if (player.EVENT_VOLUME in callbacks && lastVolume != volume) {
      var cb = callbacks[player.EVENT_VOLUME];
      cb(volume); 
    }
  };

  var updateVolume = function() {
    musicCommand('volume', function(data) {
      volume = getItem(data, 'volume', 0);
      notifyVolume();
    });
    lastVolume = volume;
  };

  var notifyShuffle = function() {
    if (player.EVENT_SHUFFLE in callbacks && lastShuffle != shuffle) {
      var cb = callbacks[player.EVENT_SHUFFLE];
      if (shuffle == 'on') {
        cb(true);
      } else {
        cb(false);
      }
    }
  };

  var updateShuffle = function() {
    musicCommand('shuffle', function(data) {
      shuffle = getItem(data, 'shuffle', 'off');
      notifyShuffle();
    });
    lastShuffle = shuffle;
  };

  var notifySinks = function() {
    if (player.EVENT_SINKS_UPDATED in callbacks && lastSinks.length != sinks.length) {
      var cb = callbacks[player.EVENT_SINKS_UPDATED];
      cb(sinks, curSink);
    }
  };

  var updateSinks = function() {
    musicCommand('sink', function(data) {
      sinks = getItem(data, 'sinks');
      notifySinks();
    });
    lastSinks = sinks;
  };

  var calcTrackPosition = function(data) {
    var s = getItem(data, 'stats'), totalSamples, occupancy, sampleRate, currMs;
    if (s) {
      totalSamples = s['total'];
      occupancy = s['occupancy'];
      sampleRate = s['rate'];
      currMs = Math.round((1000 * (totalSamples-occupancy)) / sampleRate);
    } else {
      currMs = 0;
    }
    if (getItem(track, 'track')) {
      trackLenMs = getItem(track, 'track')['duration'];
    } else {
      trackLenMs = 1;
    }

    return [trackLenMs, currMs];
  };

  var getTrackPlayState = function() {
    return getItem(track, 'state', 'stopped');
  };

  var getTrackUri = function() {
    var t = getItem(track, 'track');
    if (t) {
      return t['link'];
    } else {
      return null;
    }
  };

  var fastEvents = function() {
    updateStats();
    updateTrack();
    if (powerOn) {
      setTimeout(arguments.callee, 1000);
    }
  };

  var slowEvents = function() {
    updatePlaylist();
    updateVolume();
    updateShuffle();
    updateSinks();
    if (powerOn) {
      setTimeout(arguments.callee, 10000);
    }
  };

  // Public API exported through 'player' dictionary
  player = {

    // Events
    EVENT_TRACK_POSITION: 0,
    EVENT_TRACK_IMAGE: 1,
    EVENT_PLAYLIST: 2,
    EVENT_PLAY_STATE: 3,
    EVENT_TRACK_INFO: 4,
    EVENT_VOLUME: 5,
    EVENT_SHUFFLE: 6,
    EVENT_PLAYLIST_IMAGE: 7,
    EVENT_SINKS_UPDATED: 8,

    // API Functions
    setUrl: function(u, r) {
      url = u;
      refreshPeriod = r;
    },
    togglePower: function() {
      powerOn = !powerOn;
      if (powerOn) {
        imageCache = {};
        lastShuffle = null;
        shuffle = null;
        lastSinks = [];
        sinks = [];
        lastVolume = null;
        volume = null;
        trackState = null;
        lastTrackState = null;
        playlistHash = null;
        lastPlaylistHash = null;
        track = [];
        playlist = [];
        slowEvents();
        fastEvents();
      } else {
        musicCommand('stop', function(data){});
      }
      return powerOn;
    },
    setEventNotifier: function(event, notifier) {
      callbacks[event] = notifier;
    },
    shuffle: function(state) {
      if (powerOn) {
        if (state) {
          text = 'on';
        } else {
          text = 'off';
        }
        musicCommand('shuffle ' + text, function(data){});
      }
    },
    resetPos: function(pos) {
      if (powerOn) {
        musicCommand('reset ' + pos, function(data){});
      }
    },
    setSink: function(pos) {
      if (powerOn) {
        curSink = pos;
        musicCommand('sink ' + sinks[pos]['index'], function(data){});
      }
    },
    sendUtterance: function(utterance) {
      if (powerOn) {
        musicCommand(utterance, function(data){});
      }
    },
    setVolume: function(vol) {
      if (powerOn) {
        musicCommand('volume ' + vol, function(data){});
      }
    },
    skip: function() {
      if (powerOn) {
        musicCommand('skip', function(data){});
      }
    },
    back: function() {
      if (powerOn) {
        musicCommand('back', function(data){});
      }
    },
    clear: function() {
      if (powerOn) {
        musicCommand('clear', function(data){});
      }
    },
    stop: function() {
      if (powerOn) {
        musicCommand('stop', function(data){});
      }
    },
    play: function() {
      if (powerOn) {
        state = getTrackPlayState();
        if (state == 'playing') {
          musicCommand('pause', function(data){});
        } else if (state == 'paused') {
          musicCommand('resume', function(data){});
        } else {
          musicCommand('play', function(data){});
        }
      }
    }
  };

}( jQuery ));
