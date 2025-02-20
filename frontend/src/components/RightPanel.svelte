<script lang="ts">
  import Settings from "./tabs/Settings.svelte";
  import Summary from "./tabs/Summary.svelte";
  import Chat from "./tabs/Chat.svelte";
  import Footer from "./Footer.svelte";
  import { waveStore, currentPlaybackTime } from "../store";
  import { msToTimestamp } from "../utils";

  export let toggleTranscriptView;
  export let toggleScoreView;
  export let transcriptView;
  export let scoreView;

  let activeTab = "settings";
</script>

<div class="w-full h-full flex flex-col bg-gray-50">
  <!-- Tab Headers -->
  <div class="flex justify-center border-b bg-gray-200">
    <button
      class="px-4 py-2 {activeTab === 'settings'
        ? 'border-b-2 border-blue-300 bg-gray-50 relative after:absolute after:bottom-[-1px] after:left-0 after:right-0 after:h-[1px] after:bg-gray-50'
        : 'hover:bg-gray-100'}"
      on:click={() => (activeTab = "settings")}
    >
      <div class="flex items-center gap-2">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fill-rule="evenodd"
            d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z"
            clip-rule="evenodd"
          />
        </svg>
        Settings
      </div>
    </button>
    <button
      class="px-4 py-2 {activeTab === 'summary'
        ? 'border-b-2 border-blue-300 bg-gray-50 relative after:absolute after:bottom-[-1px] after:left-0 after:right-0 after:h-[1px] after:bg-gray-50'
        : 'hover:bg-gray-100'}"
      on:click={() => (activeTab = "summary")}
    >
      <div class="flex items-center gap-2">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
          <path
            fill-rule="evenodd"
            d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z"
            clip-rule="evenodd"
          />
        </svg>
        Summary
      </div>
    </button>
    <button
      class="px-4 py-2 {activeTab === 'chat'
        ? 'border-b-2 border-blue-300 bg-gray-50 relative after:absolute after:bottom-[-1px] after:left-0 after:right-0 after:h-[1px] after:bg-gray-50'
        : 'hover:bg-gray-100'}"
      on:click={() => (activeTab = "chat")}
    >
      <div class="flex items-center gap-2">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fill-rule="evenodd"
            d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z"
            clip-rule="evenodd"
          />
        </svg>
        Chat
      </div>
    </button>
  </div>

  <!-- Tab Content -->
  <div class="flex-1 overflow-y-auto p-4">
    {#if activeTab === "settings"}
      <Settings
        {toggleTranscriptView}
        {toggleScoreView}
        {transcriptView}
        {scoreView}
      />
    {:else if activeTab === "summary"}
      <Summary />
    {:else if activeTab === "chat"}
      <Chat />
    {/if}
  </div>

  <!-- Footer -->
  <div class="mt-auto border-t bg-gray-200">
    <Footer />
  </div>
</div>
