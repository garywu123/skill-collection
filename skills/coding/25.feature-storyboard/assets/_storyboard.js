(() => {
  "use strict";

  const boards = document.querySelectorAll("[data-storyboard][data-interactive]");

  for (const board of boards) {
    const states = new Map(
      Array.from(board.querySelectorAll("[data-state][id]"), state => [state.id, state])
    );

    if (states.size === 0) {
      continue;
    }

    const initialId = board.dataset.initial;
    const fallbackId = states.keys().next().value;

    const activate = (requestedId, moveFocus = true) => {
      const target = states.get(requestedId) ?? states.get(fallbackId);

      for (const state of states.values()) {
        const active = state === target;
        state.toggleAttribute("data-active", active);
        state.setAttribute("aria-hidden", String(!active));
      }

      if (moveFocus) {
        target.focus({ preventScroll: true });
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    };

    for (const control of board.querySelectorAll("[data-interactive-control]")) {
      control.hidden = false;
    }

    board.addEventListener("click", event => {
      if (!(event.target instanceof Element)) {
        return;
      }

      const reset = event.target.closest("[data-reset]");
      if (reset && board.contains(reset)) {
        event.preventDefault();
        activate(initialId ?? fallbackId);
        return;
      }

      const trigger = event.target.closest("[data-go]");
      if (!trigger || !board.contains(trigger)) {
        return;
      }

      const targetId = trigger.getAttribute("data-go");
      if (!targetId || !states.has(targetId)) {
        return;
      }

      event.preventDefault();
      activate(targetId);
    });

    activate(initialId ?? fallbackId, false);
  }
})();
