<script lang="ts">
  import {
    mediaStoreURL,
    fileInfo,
    waveStore,
    currentPlaybackTime,
    subtitleTrackStore,
    transcriptTrackStore,
  } from "../../store";
  import { msToTimestamp, newSessionMetadata } from "../../utils";
  import type { SubtitleNode } from "../../utils";

  export let toggleTranscriptView;
  export let toggleScoreView;
  export let transcriptView;
  export let scoreView;

  // Helper function to convert iterator to array
  function iteratorToArray<T>(iterator: Iterator<T>): T[] {
    const array: T[] = [];
    let result = iterator.next();
    while (!result.done) {
      array.push(result.value);
      result = iterator.next();
    }
    return array;
  }

  // Get current segment number based on playback time
  $: currentSegmentNumber = (() => {
    if (!$waveStore) return 0;

    const currentTrack = transcriptView
      ? $transcriptTrackStore
      : $subtitleTrackStore;
    const segments = iteratorToArray(currentTrack.iterate());

    const currentTime = $currentPlaybackTime * 1000; // Convert to ms
    for (let i = 0; i < segments.length; i++) {
      const segment = segments[i];
      if (
        currentTime >= segment.data.start &&
        currentTime <= segment.data.end
      ) {
        return i + 1; // Add 1 since we want to display 1-based index
      }
    }
    return 0;
  })();

  // Get total segments count
  $: totalSegments = transcriptView
    ? iteratorToArray($transcriptTrackStore.iterate()).length
    : iteratorToArray($subtitleTrackStore.iterate()).length;

  // Get metadata for display with dynamic segment count
  $: metadata = $waveStore
    ? {
        EOT: msToTimestamp($waveStore.getDuration() * 1000),
        CUR: msToTimestamp($currentPlaybackTime * 1000),
        SPD: $waveStore.getPlaybackRate() + "x",
        SEG: `${currentSegmentNumber || "-"}/${totalSegments}`,
      }
    : {};

  function handleMediaSelect(event: any) {
    const selectedMedia = event.target.files[0];
    if (selectedMedia) {
      let fileURL = URL.createObjectURL(selectedMedia);
      fileInfo.update((e) => ({
        ...e,
        mediaFileName: selectedMedia.name,
      }));
      mediaStoreURL.set(fileURL);
    }
  }

  function handleTranscriptSelect(event: any) {
    const file = event.target.files[0];
    if (file) {
      // Add your transcript handling logic here
      fileInfo.update((e) => ({
        ...e,
        transcriptFileName: file.name,
      }));
    }
  }

  function handleExport() {
    // Add your export logic here
  }
</script>

<div class="flex flex-col gap-6 p-4">
  <!-- Media Import Section -->
  <div class="flex flex-col gap-4">
    <h2 class="text-lg font-semibold text-center">Media Import</h2>

    <div class="flex flex-col gap-3 items-center">
      <!-- Load Audio -->
      <div class="flex flex-col gap-2 w-full max-w-sm">
        <input
          class="hidden"
          id="media"
          type="file"
          accept="video/*, audio/*"
          on:change={handleMediaSelect}
        />
        <label
          for="media"
          class="flex items-center justify-center gap-2 px-4 py-2 bg-white rounded-md border border-gray-300 hover:bg-gray-50 cursor-pointer w-full"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            ><path
              fill="currentColor"
              d="M10.75 18.692q.816 0 1.379-.563q.563-.564.563-1.379v-3.98h2.731v-1.54h-3.5v4.087q-.236-.257-.53-.383q-.293-.126-.643-.126q-.815 0-1.379.563q-.563.564-.563 1.379t.563 1.379q.564.563 1.379.563M6.616 21q-.691 0-1.153-.462T5 19.385V4.615q0-.69.463-1.152T6.616 3H14.5L19 7.5v11.885q0 .69-.462 1.153T17.384 21zM14 8V4H6.616q-.231 0-.424.192T6 4.615v14.77q0 .23.192.423t.423.192h10.77q.23 0 .423-.192t.192-.424V8zM6 4v4zv16z"
            /></svg
          >
          Load Audio
        </label>
        {#if $fileInfo.mediaFileName}
          <div class="text-sm text-gray-600 text-center">
            {$fileInfo.mediaFileName}
          </div>
        {/if}
      </div>

      <!-- Load Transcript -->
      <div class="flex flex-col gap-2 w-full max-w-sm">
        <input
          class="hidden"
          id="transcriptfile"
          type="file"
          accept=".json,.srt,.vtt"
          on:change={handleTranscriptSelect}
        />
        <label
          for="transcriptfile"
          class="flex items-center justify-center gap-2 px-4 py-2 bg-white rounded-md border border-gray-300 hover:bg-gray-50 cursor-pointer w-full"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            ><path
              fill="currentColor"
              d="M8.5 11.5v-1h7v1zm0-4v-1h7v1zm-2.5 7h7.5q.61 0 1.12.265q.509.264.876.743L18 18.758V4.616q0-.27-.173-.443T17.385 4H6.615q-.269 0-.442.173T6 4.616zm.616 5.5h11.069l-2.975-3.883q-.227-.296-.536-.457q-.308-.16-.674-.16H6v3.885q0 .269.173.442t.443.173m10.769 1H6.615q-.69 0-1.152-.462T5 19.385V4.615q0-.69.463-1.152T6.616 3h10.769q.69 0 1.153.463T19 4.616v14.769q0 .69-.462 1.153T17.384 21M6 20V4zm0-4.5v-1z"
            /></svg
          > Load Transcript
        </label>
        {#if $fileInfo.transcriptFileName}
          <div class="text-sm text-gray-600 text-center">
            {$fileInfo.transcriptFileName}
          </div>
        {/if}
      </div>
    </div>
  </div>

  <!-- Media Export Section -->
  <div class="flex flex-col gap-4">
    <h2 class="text-lg font-semibold text-center">Media Export</h2>
    <div class="grid grid-cols-2 gap-3 max-w-lg mx-auto">
      <button
        class="flex items-center justify-center gap-2 px-4 py-2 bg-white rounded-md border border-gray-300 hover:bg-gray-50"
        on:click={handleExport}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          ><path
            fill="currentColor"
            d="m12 15.577l-3.539-3.538l.708-.72L11.5 13.65V5h1v8.65l2.33-2.33l.709.719zM6.616 19q-.691 0-1.153-.462T5 17.384v-2.423h1v2.423q0 .231.192.424t.423.192h10.77q.23 0 .423-.192t.192-.424v-2.423h1v2.423q0 .691-.462 1.153T17.384 19z"
          /></svg
        >
        Export Audio
      </button>

      <button
        class="flex items-center justify-center gap-2 px-4 py-2 bg-white rounded-md border border-gray-300 hover:bg-gray-50"
        on:click={handleExport}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          ><path
            fill="currentColor"
            d="m12 15.577l-3.539-3.538l.708-.72L11.5 13.65V5h1v8.65l2.33-2.33l.709.719zM6.616 19q-.691 0-1.153-.462T5 17.384v-2.423h1v2.423q0 .231.192.424t.423.192h10.77q.23 0 .423-.192t.192-.424v-2.423h1v2.423q0 .691-.462 1.153T17.384 19z"
          /></svg
        >
        Export Transcript
      </button>
    </div>
  </div>

  <!-- View Option -->
  <div class="flex flex-col gap-4">
    <h2 class="text-lg font-semibold text-center">View Options</h2>
    <div class="grid grid-cols-2 gap-3 max-w-lg mx-auto">
      <button
        class="flex items-center justify-center gap-2 px-4 py-2 bg-white rounded-md border border-gray-300 hover:bg-gray-50"
        on:click={toggleTranscriptView}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          ><path
            fill="currentColor"
            d="M4 11V4h7v7zm0 9v-7h7v7zm9-9V4h7v7zm0 9v-7h7v7zM5 10h5V5H5zm9 0h5V5h-5zm0 9h5v-5h-5zm-9 0h5v-5H5zm5-9"
          /></svg
        >
        {transcriptView ? "Transcript Mode" : "Subtitle Mode"}
      </button>

      <button
        class="flex items-center justify-center gap-2 px-4 py-2 bg-white rounded-md border border-gray-300 hover:bg-gray-50"
        on:click={toggleScoreView}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          ><path
            fill="currentColor"
            d="M4.714 19.98L4 19.268l5.1-5.094H6.058v-1h4.75v4.75h-1v-3.042zm8.478-9.191v-4.75h1V9.08l5.095-5.1l.713.713l-5.1 5.095h3.042v1z"
          /></svg
        >
        {scoreView ? "Hide Confidence" : "Show Confidence"}
      </button>
    </div>
  </div>

  <!-- Model Selection -->
  <div class="flex flex-col gap-4">
    <h2 class="text-lg font-semibold text-center">Model Selection</h2>
    <div class="flex flex-col gap-3 max-w-lg mx-auto w-full">
      <select
        class="w-full px-4 py-2 bg-white rounded-md border border-gray-300 text-center appearance-none cursor-pointer"
        style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23131313%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.7rem top 50%; background-size: 0.65rem auto;"
      >
        <option value="" disabled selected hidden>Select TTS Model</option>
        <option>Coqui TTS</option>
        <option>FastPitch</option>
        <option>Tacotron 2</option>
        <option>YourTTS</option>
      </select>

      <select
        class="w-full px-4 py-2 bg-white rounded-md border border-gray-300 text-center appearance-none cursor-pointer"
        style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23131313%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.7rem top 50%; background-size: 0.65rem auto;"
      >
        <option value="" disabled selected hidden>Select LLM Model</option>
        <option>GPT-3.5</option>
        <option>GPT-4</option>
        <option>Claude</option>
        <option>LLaMA</option>
      </select>
    </div>
  </div>

  <div class="border-t"></div>

  <!-- Status Information -->
  <div class="flex flex-col gap-4">
    <div class="font-mono text-xs">
      <div class="mb-2 font-semibold">Status Information</div>
      {#if $waveStore}
        <div>
          <b>End Time:</b>
          {metadata.EOT}
        </div>
        <div>
          <b>Current Time:</b>
          {metadata.CUR}
        </div>
        <div><b>Speed:</b> {metadata.SPD}</div>
        <div><b>Segments:</b> {metadata.SEG}</div>
      {/if}
    </div>
  </div>

  <div class="border-t"></div>

  <!-- Help Section -->
  <div class="flex flex-col gap-4">
    <div class="font-mono text-xs">
      <div class="mb-2 font-semibold">Help 💡</div>
      <ul class="list-disc list-inside space-y-1">
        <li>
          Use <kbd
            class="px-1 py-0.5 bg-gray-100 border border-gray-300 rounded"
            >space</kbd
          > to play/pause
        </li>
        <li>
          Edit/Add segments use
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4 inline ml-1"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            fill="none"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10"
            />
          </svg>
        </li>
        <li>
          Remove segments use
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4 inline ml-1"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            fill="none"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"
            />
          </svg>
        </li>
        <li>Change playback speed with (n)x</li>
        <li>Toggle between transcript & subtitle</li>
        <li>Toggle confidence (if applicable)</li>
      </ul>
    </div>
  </div>
</div>
