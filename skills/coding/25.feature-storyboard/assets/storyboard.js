(() => {
  "use strict";

  const regions = [".sb-sidebar", ".sb-panel", ".sb-inspector"];

  // Puts the named shell from shell.js around each state's .sb-content,
  // region overrides, and overlays, so every state is a whole screen.
  const mountShell = board => {
    const markup = window.SB_SHELLS?.[board.dataset.shell];
    if (!markup) {
      const error = document.createElement("p");
      error.className = "sb-banner";
      error.textContent = `Storyboard shell "${board.dataset.shell}" not found. Load shell.js before storyboard.js and check the name.`;
      board.prepend(error);
      return;
    }

    for (const device of board.querySelectorAll("[data-state] > .sb-device")) {
      const content = device.querySelector(":scope > .sb-content");
      const overrides = regions.map(region => device.querySelector(`:scope > ${region}`));
      const overlays = Array.from(device.children)
        .filter(child => child !== content && !overrides.includes(child));

      const template = document.createElement("template");
      template.innerHTML = markup;
      const shell = template.content;

      const title = shell.querySelector('[data-slot="title"]');
      if (title) {
        title.textContent = device.dataset.title ?? "";
      }
      for (const item of shell.querySelectorAll("[data-nav-key]")) {
        item.classList.toggle("sb-selected", item.dataset.navKey === device.dataset.nav);
      }
      const window_ = shell.querySelector(".sb-window");
      regions.forEach((region, index) => {
        const override = overrides[index];
        if (override && window_) {
          const existing = window_.querySelector(`:scope > ${region}`);
          existing ? existing.replaceWith(override) : window_.append(override);
        }
      });
      const slot = shell.querySelector('[data-slot="content"]');
      if (slot && content) {
        slot.replaceWith(content);
      }

      device.replaceChildren(shell, ...overlays);
    }
  };

  // Lists each state's outgoing transitions and marks end and unreached states.
  const buildOverview = (board, states, initialId) => {
    const reached = new Set(
      Array.from(board.querySelectorAll("[data-go]"), link => link.dataset.go)
    );

    for (const state of states.values()) {
      const list = document.createElement("ul");
      list.className = "sb-overview";
      const add = text => {
        const item = document.createElement("li");
        item.textContent = text;
        list.append(item);
      };

      const links = state.querySelectorAll("[data-go]");
      for (const link of links) {
        add(`${link.dataset.transition ?? "?"} · ${link.textContent.trim()} → ${link.dataset.go}`);
      }
      if (links.length === 0) {
        add("End state: no outgoing transition");
      }
      if (state.id !== initialId && !reached.has(state.id)) {
        add("Not reached by any transition");
      }
      state.append(list);
    }
  };

  for (const board of document.querySelectorAll("[data-storyboard][data-shell]")) {
    mountShell(board);
  }

  const boards = document.querySelectorAll("[data-storyboard][data-interactive]");

  for (const board of boards) {
    const states = new Map(
      Array.from(board.querySelectorAll("[data-state][id]"), state => [state.id, state])
    );

    if (states.size === 0) {
      continue;
    }

    const fallbackId = states.keys().next().value;
    const initialId = board.dataset.initial ?? fallbackId;
    let currentId = initialId;

    buildOverview(board, states, initialId);

    const activate = (requestedId, moveFocus = true) => {
      const target = states.get(requestedId) ?? states.get(fallbackId);
      currentId = target.id;
      board.removeAttribute("data-overview");

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

    const showOverview = () => {
      board.toggleAttribute("data-overview", true);
      for (const state of states.values()) {
        state.removeAttribute("aria-hidden");
      }
    };

    board.toggleAttribute("data-running", true);

    for (const control of board.querySelectorAll("[data-interactive-control]")) {
      control.hidden = false;
    }

    board.addEventListener("click", event => {
      if (!(event.target instanceof Element)) {
        return;
      }

      const toggle = event.target.closest("[data-overview-toggle]");
      if (toggle && board.contains(toggle)) {
        event.preventDefault();
        board.hasAttribute("data-overview") ? activate(currentId, false) : showOverview();
        return;
      }

      const reset = event.target.closest("[data-reset]");
      if (reset && board.contains(reset)) {
        event.preventDefault();
        activate(initialId);
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

    const linkedId = decodeURIComponent(location.hash.slice(1));
    activate(states.has(linkedId) ? linkedId : initialId, false);
    if (linkedId === "overview") {
      showOverview();
    }
  }
})();
