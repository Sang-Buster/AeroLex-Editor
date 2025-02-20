<script lang="ts">
  import { waveStore, isPlayable, currentPlaybackTime } from "../store";

  let currentSpeed = 1;

  const updateCurrentTimestamp = (e: Event) => {
    $waveStore.setTime((e.target as HTMLInputElement).value);
  };

  const pbSpeed = (speed: number, increment: boolean = true): void => {
    if (speed) {
      $waveStore.setPlaybackRate(speed);
      currentSpeed = speed;
      return;
    }
    if (increment) {
      const newSpeed = $waveStore.getPlaybackRate() + 0.5;
      $waveStore.setPlaybackRate(newSpeed);
      currentSpeed = newSpeed;
    } else {
      const newSpeed = $waveStore.getPlaybackRate() - 0.5;
      $waveStore.setPlaybackRate(newSpeed);
      currentSpeed = newSpeed;
    }
  };

  const jumpTime = (seconds: number) => {
    const newTime = $currentPlaybackTime + seconds;
    const duration = $waveStore.getDuration();
    if (newTime >= 0 && newTime <= duration) {
      $waveStore.setTime(newTime);
    }
  };

  const togglePlay = () => {
    $waveStore.playPause();
  };

  const restart = () => {
    $waveStore.setTime(0);
  };

  let isPlaying = false;
  $: if ($waveStore) {
    $waveStore.on("play", () => (isPlaying = true));
    $waveStore.on("pause", () => (isPlaying = false));
  }
  $: {
    if ($waveStore) {
      currentSpeed = $waveStore.getPlaybackRate();
    }
  }
  $: duration = $waveStore ? $waveStore.getDuration() * 1000 : 0;

  const formatTime = (timeInSeconds: number) => {
    const ms = timeInSeconds * 1000; // Convert seconds to milliseconds
    const hours = Math.floor(ms / 3_600_000);
    const minutes = Math.floor((ms % 3_600_000) / 60_000);
    const seconds = Math.floor((ms % 60_000) / 1_000);
    const milliseconds = Math.floor(ms % 1000);

    return `${hours.toString().padStart(2, "0")}:${minutes
      .toString()
      .padStart(2, "0")}:${seconds.toString().padStart(2, "0")}.${milliseconds
      .toString()
      .padStart(3, "0")}`;
  };
</script>

<div class="flex w-full items-center bg-gray-100 h-26 shadow px-6 pb-4 pt-4">
  {#if $isPlayable}
    <div class="flex flex-col w-full gap-2">
      <!-- Timeline and controls -->
      <div class="flex items-center gap-4 w-full">
        <!-- Control buttons -->
        <div class="flex items-center gap-2">
          <button
            on:click={restart}
            class="p-2 hover:bg-gray-200 rounded-full"
            title="Restart"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              ><path
                fill="currentColor"
                d="M11 19.912q-2.602-.356-4.301-2.32Q5 15.626 5 13q0-1.4.554-2.682t1.523-2.272l.714.713q-.893.831-1.342 1.927T6 13q0 2.2 1.41 3.868q1.41 1.669 3.59 2.044zm2 .038v-1q2.156-.477 3.578-2.123T18 13q0-2.5-1.75-4.25T12 7h-.633l1.6 1.6l-.708.708L9.452 6.5l2.808-2.808l.707.708l-1.6 1.6H12q2.927 0 4.964 2.036T19 13q0 2.621-1.709 4.566Q15.583 19.512 13 19.95"
              /></svg
            >
          </button>

          <button
            on:click={() => jumpTime(-3)}
            class="p-2 hover:bg-gray-200 rounded-full"
            title="Backward 3s"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              ><path
                fill="currentColor"
                d="M19.904 16.616L12.98 12l6.923-4.615zm-8.885 0L4.096 12l6.923-4.615z"
              /></svg
            >
          </button>

          <button
            on:click={togglePlay}
            class="p-2 hover:bg-gray-200 rounded-full"
            title={isPlaying ? "Pause" : "Play"}
          >
            {#if isPlaying}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                ><path
                  fill="currentColor"
                  d="M14 18V6h3.5v12zm-7.5 0V6H10v12z"
                /></svg
              >
            {:else}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                ><path
                  fill="currentColor"
                  d="M9 17.192V6.808L17.154 12z"
                /></svg
              >
            {/if}
          </button>

          <button
            on:click={() => jumpTime(3)}
            class="p-2 hover:bg-gray-200 rounded-full"
            title="Forward 3s"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              ><path
                fill="currentColor"
                d="M4.096 16.616V7.385L11.02 12zm8.885 0V7.385L19.904 12z"
              /></svg
            >
          </button>
        </div>

        <!-- Timeline -->
        <div class="flex-1">
          <input
            class="w-full accent-blue-500"
            type="range"
            min="0"
            on:change={updateCurrentTimestamp}
            max={$waveStore.getDuration()}
            value={$currentPlaybackTime}
          />
        </div>

        <!-- Speed and volume controls -->
        <div class="flex items-center gap-2">
          <button
            on:click={() => pbSpeed(null, false)}
            class="p-2 hover:bg-gray-200 rounded-full"
            title="Decrease speed"
          >
            🐢
          </button>

          <button
            on:click={() => pbSpeed(1)}
            class="p-2 hover:bg-gray-200 rounded-full"
            title="Reset speed"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              ><path
                fill="currentColor"
                d="M3.616 20q-.691 0-1.153-.462T2 18.384V5.616q0-.691.463-1.153T3.616 4h16.769q.69 0 1.153.463T22 5.616v12.769q0 .69-.462 1.153T20.385 20zm0-1h16.769q.23 0 .423-.192t.192-.424V5.616q0-.231-.192-.424T20.385 5H3.615q-.23 0-.423.192T3 5.616v12.769q0 .23.192.423t.423.192M3 19V5zM7.5 8.5V16q0 .214.143.357T8 16.5t.357-.143T8.5 16V8.308q0-.348-.23-.578t-.578-.23H6q-.213 0-.357.143T5.5 8t.143.357T6 8.5zm7.75 4.248l2.077 3.514q.067.104.171.17q.104.068.238.068q.27 0 .423-.235q.154-.236 0-.488l-2.351-4.008l2.107-3.565q.135-.233-.003-.468q-.137-.236-.406-.236q-.135 0-.239.067t-.17.171l-1.828 3.11l-1.827-3.11q-.067-.104-.17-.17q-.105-.068-.24-.068q-.268 0-.422.235q-.154.236 0 .488l2.102 3.585l-2.358 3.988q-.135.233.003.468q.137.236.407.236q.134 0 .238-.067q.104-.068.171-.172z"
              /></svg
            >
          </button>

          <button
            on:click={() => pbSpeed(null, true)}
            class="p-2 hover:bg-gray-200 rounded-full"
            title="Increase speed"
          >
            🐰
          </button>
        </div>
      </div>

      <!-- Status info -->
      <div class="grid grid-cols-3 items-center text-sm text-gray-600 px-6">
        <div class="text-left">
          <span>{currentSpeed.toFixed(1)}x</span>
        </div>
        <div class="text-center">
          <span>{isPlaying ? "Playing" : "Paused"}</span>
        </div>
        <div class="text-right">
          {formatTime($currentPlaybackTime)} / {formatTime(
            $waveStore?.getDuration() || 0,
          )}
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  input[type="range"] {
    -webkit-appearance: none;
    appearance: none;
    background: transparent;
  }

  input[type="range"]::-webkit-slider-runnable-track {
    width: 100%;
    height: 4px;
    background: #e5e7eb;
  }

  input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    height: 16px;
    width: 16px;
    border-radius: 50%;
    background: #3b82f6;
    margin-top: -6px;
    cursor: pointer;
  }

  input[type="range"]::-moz-range-track {
    width: 100%;
    height: 4px;
    background: #e5e7eb;
  }

  input[type="range"]::-moz-range-thumb {
    height: 16px;
    width: 16px;
    border-radius: 50%;
    background: #3b82f6;
    cursor: pointer;
    border: none;
  }

  input[type="range"]::-moz-range-progress {
    height: 4px;
    background: #bfdbfe;
  }

  input[type="range"]::-ms-track {
    width: 100%;
    height: 4px;
    background: #e5e7eb;
  }

  input[type="range"]::-ms-fill-lower {
    background: #bfdbfe;
  }

  input[type="range"]::-ms-thumb {
    height: 16px;
    width: 16px;
    border-radius: 50%;
    background: #3b82f6;
    cursor: pointer;
    border: none;
  }
</style>
