import { writable, get } from "svelte/store";
import {
  subTitleTrackFromSegmentData,
  segmentToNodeData,
  sanitizeContent,
  SubtitleTrack,
  SubtitleNode,
  msToTimestamp,
} from "./utils";
import type { TranscribedData } from "./types";
import { nanoid } from "nanoid";

// Initialize all stores first
const errListStore = createErrorStore();
const rawTranscriptDataStore = writable({});
const currentPlaybackTime = writable(0);
const wordLevelData = writable(true);
const scoreView = writable(false);
const waveStore = writable(null);
const mediaStoreURL = writable("/audio/log.mp3");
const isPlayable = writable(false);
const fileInfo = writable({
  mediaFileName: "log.mp3",
  transcriptFileName: "log.json",
});

// Declare track variables
let subtitleTrackStore = createSubtitleTrackStore(new SubtitleTrack());
let transcriptTrackStore = createSubtitleTrackStore(new SubtitleTrack());
let strack: SubtitleTrack, ttrack: SubtitleTrack;

// Load initial data
try {
  const response = await fetch("/text/log.json");
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  const sampletranscriptdata = await response.json();
  rawTranscriptDataStore.set(sanitizeContent(sampletranscriptdata));

  [strack, ttrack] = subTitleTrackFromSegmentData(
    get(rawTranscriptDataStore) as TranscribedData[],
  );
  subtitleTrackStore = createSubtitleTrackStore(strack);
  transcriptTrackStore = createSubtitleTrackStore(ttrack);
} catch (e) {
  console.error("Failed to load transcript data:", e);
  errListStore.addToList(e.message);
}

// Store creation functions
function createErrorStore() {
  const { subscribe, set, update } = writable([]);

  return {
    subscribe,
    set,
    addToList: (error: string) => {
      update((i) => [...i, error]);
    },
  };
}

function createSubtitleTrackStore(track: SubtitleTrack) {
  const { subscribe, update, set } = writable(track);

  // Helper function to update raw transcript data
  const updateRawTranscript = (track: SubtitleTrack) => {
    const segments = Array.from(track.iterate() as Iterable<SubtitleNode>).map(
      (node) => ({
        score: node.data.score,
        start: msToTimestamp(node.data.start),
        end: msToTimestamp(node.data.end),
        text: node.data.text,
        words:
          node.data.words?.map((word) => ({
            start: msToTimestamp(word.start as number),
            end: msToTimestamp(word.end as number),
            text: word.text,
            score: word.score,
          })) || [],
      }),
    );
    rawTranscriptDataStore.set(segments);
  };

  return {
    subscribe,
    set: (newTrack: SubtitleTrack) => {
      set(newTrack);
      updateRawTranscript(newTrack);
    },
    appendAfterSegment: (node: SubtitleNode) => {
      resetNodeNextPrev(node);
      update((t) => {
        let s: TranscribedData = {
          score: 1,
          start: node.data.end,
          end: node.maxOffset(),
          text: "placeholder text added after",
          words: [],
        };
        let nd = segmentToNodeData(s);
        t.appendAfterNode(nd, node);
        updateRawTranscript(t);
        return t;
      });
    },
    appendBeforeSegment: (node: SubtitleNode) => {
      resetNodeNextPrev(node);
      update((t) => {
        let s: TranscribedData = {
          score: 1,
          start: node.minOffset(),
          end: node.data.start,
          text: "placeholder text added before",
          words: [],
        };
        let nd = segmentToNodeData(s);
        t.appendBeforeNode(nd, node);
        updateRawTranscript(t);
        return t;
      });
    },
    removeSegment: (node: SubtitleNode) => {
      node.data.uuid = nanoid();
      if (node.prev) {
        node.prev.data.uuid = nanoid();
      }
      if (node.next) {
        node.next.data.uuid = nanoid();
      }
      update((t) => {
        if (!node.prev) {
          // head
          t.removeFromFront();
        } else if (!node.next) {
          // tail
          t.removeFromBack();
        } else {
          node.yeetSelf();
          t.size--;
        }
        updateRawTranscript(t);
        return t;
      });
    },
    toggleEditModeForSegment: (node: SubtitleNode) => {
      node.data.offsetEditMode = !node.data.offsetEditMode;
      resetNodeNextPrev(node, true);
      update((t) => t);
    },
    updateTsForSegment: (
      node: SubtitleNode,
      ts: { start: number; end: number },
    ) => {
      node.data.start = ts.start;
      node.data.end = ts.end;
      resetNodeNextPrev(node);
      update((t) => {
        updateRawTranscript(t);
        return t;
      });
    },
    updateTextForSegment: (node: SubtitleNode, text: string) => {
      node.data.text = text;
      resetNodeNextPrev(node);
      update((t) => {
        updateRawTranscript(t);
        return t;
      });
    },
    resetTrack: (node?: SubtitleNode) => {
      if (node) {
        resetNodeNextPrev(node);
      }
      update((t) => {
        updateRawTranscript(t);
        return t;
      });
    },
  };
}

// why?
// TODO: Come back to this later and convert into a github issue
// - contenteditable on lage number causes slowness if span inside div, normal text worked fine
// - works on chrome not on ff
// - anyway with immutable=false (default), svelte will render all of the list, not ideal
// - we cannot keep the key just the hash of the content because we want linked
//   nodes to be updated as well when we update current node
// - so we update current, prev and next uuid so that each re-renders only those
//   as that's used as the key
const resetNodeNextPrev = (
  node: SubtitleNode,
  currentNodeOnly: boolean = false,
) => {
  node.data.uuid = nanoid();
  if (!currentNodeOnly) {
    if (node.prev) {
      node.prev.data.uuid = nanoid();
    }
    if (node.next) {
      node.next.data.uuid = nanoid();
    }
  }
};

// Exports
export {
  errListStore,
  subtitleTrackStore,
  transcriptTrackStore,
  currentPlaybackTime,
  rawTranscriptDataStore,
  wordLevelData,
  scoreView,
  waveStore,
  mediaStoreURL,
  isPlayable,
  fileInfo,
};
