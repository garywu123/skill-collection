// Storyboard app shells. Markup only; storyboard.js mounts the shell a board names in data-shell.
// Slots: data-slot="title" takes the state's data-title; data-slot="content" takes its .sb-content.
// Nav: a state's data-nav selects the item with the matching data-nav-key.
window.SB_SHELLS = {
  desktop: `
    <header class="sb-topbar sb-row">
      <span>APP</span>
      <span class="sb-muted" data-slot="title"></span>
    </header>
    <div class="sb-window">
      <nav class="sb-nav sb-stack" aria-label="Main">
        <span class="sb-nav-item" data-nav-key="home">⌂<small>Home</small></span>
        <span class="sb-nav-item" data-nav-key="records">≡<small>Records</small></span>
        <span class="sb-nav-item" data-nav-key="settings">⚙<small>Settings</small></span>
      </nav>
      <div data-slot="content"></div>
    </div>`,
  phone: `
    <header class="sb-topbar sb-row">
      <span data-slot="title"></span>
    </header>
    <div data-slot="content"></div>`
};
