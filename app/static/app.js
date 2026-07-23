// Intercept .ajax-form submits so toggling/deleting doesn't do a full page
// navigation (which resets scroll position). Submits the form in the
// background, then swaps in the freshly rendered <main> content in place.
document.addEventListener("submit", async (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement) || !form.classList.contains("ajax-form")) {
        return;
    }
    event.preventDefault();

    const scrollY = window.scrollY;
    try {
        await fetch(form.action, { method: "POST", body: new FormData(form) });
        const resp = await fetch(window.location.pathname + window.location.search);
        const html = await resp.text();
        const newMain = new DOMParser().parseFromString(html, "text/html").querySelector("main");
        if (newMain) {
            document.querySelector("main").replaceWith(newMain);
        }
    } catch (err) {
        // Network hiccup — fall back to a normal navigation so the action still happens.
        form.submit();
        return;
    }
    window.scrollTo(0, scrollY);
});
