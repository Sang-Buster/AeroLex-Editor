<script lang="ts">
  import {
    currentPlaybackTime,
    waveStore,
    mediaStoreURL,
    isPlayable,
  } from "../store";
  import { onMount } from "svelte";
  import WaveSurfer from "wavesurfer.js";

  const isContentEditable = (element): boolean => {
    if (!element) return false;
    return (
      element.isContentEditable ||
      (element.parentNode && isContentEditable(element.parentNode))
    );
  };

  function handleSpaceKeyPress(event: any) {
    if (event.key === " ") {
      if (!isContentEditable(event.target)) {
        event.preventDefault();
        $waveStore.playPause();
      }
    }
  }

  const initWaveForm = () => {
    waveStore.set(
      WaveSurfer.create({
        container: document.querySelector("#waveform") as HTMLElement,
        waveColor: "#78716c",
        progressColor: "#5ea2fb",
        fillParent: true,
        url: $mediaStoreURL,
        interact: false,
        barWidth: 2,
        barGap: 1,
        barAlign: "top",
        barRadius: 2,
      }),
    );
    $waveStore.setVolume(1);
    $waveStore.on("timeupdate", (currentTime: number) => {
      currentPlaybackTime.set(currentTime);
    });
    $waveStore.on("ready", () => {
      isPlayable.set(true);
    });
  };

  onMount(() => {
    initWaveForm();
    window.addEventListener("keydown", handleSpaceKeyPress);
    return () => {
      window.removeEventListener("keydown", handleSpaceKeyPress);
      $waveStore.destroy();
    };
  });
</script>

<div id="waveform" class="absolute inset-0"></div>

<style>
  #waveform {
    transform: rotate(90deg);
    transform-origin: left top;
    position: absolute;
    top: 0;
    left: 0;
    height: 60px;
    width: 100%; /* Make sure it fills the container */
    margin: 0;
  }
</style>
