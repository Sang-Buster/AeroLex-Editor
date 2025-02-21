<script lang="ts">
  import MainEditor from "./components/MainEditor.svelte";
  import ErrorList from "./components/ErrorList.svelte";
  import BottomPlayer from "./components/BottomPlayer.svelte";
  import RightPanel from "./components/RightPanel.svelte";
  import {
    subtitleTrackStore,
    errListStore,
    transcriptTrackStore,
    scoreView,
  } from "./store";

  let transcriptView = false;
  const toggleScoreView = () => {
    $scoreView = !$scoreView;
    currentTrack.resetTrack();
  };
  const toggleTranscriptView = () => {
    transcriptView = !transcriptView;
    currentTrack.resetTrack();
  };
  $: currentTrack = transcriptView ? transcriptTrackStore : subtitleTrackStore;
</script>

<main>
  <div class="h-screen flex flex-col">
    <div class="flex flex-1 overflow-hidden">
      <div class="w-3/4 flex flex-col">
        {#if $errListStore.length === 0}
          <MainEditor {currentTrack} />
          <BottomPlayer />
        {/if}
      </div>

      <div class="w-1/4 border-l">
        <ErrorList errList={$errListStore} />
        <RightPanel
          {toggleTranscriptView}
          {toggleScoreView}
          {transcriptView}
          scoreView={$scoreView}
        />
      </div>
    </div>
  </div>
</main>

<style>
  :global(#waveform) {
    transform: rotate(90deg);
    position: absolute;
    top: 0;
    bottom: 0;
    right: 0;
  }

  :global(.lds-ripple) {
    display: inline-block;
    position: relative;
    width: 80px;
    height: 80px;
  }
  :global(.lds-ripple div) {
    position: absolute;
    border: 4px solid #000;
    opacity: 1;
    border-radius: 50%;
    animation: lds-ripple 1s cubic-bezier(0, 0.2, 0.8, 1) infinite;
  }
  :global(.lds-ripple div:nth-child(2)) {
    animation-delay: -0.5s;
  }
</style>
