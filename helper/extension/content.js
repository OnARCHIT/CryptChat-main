// Monitors clicks on links/images
document.addEventListener("click", async (e) => {
  const target = e.target;

  // If a link
  if (target.tagName === "A" && target.href) {
    e.preventDefault(); // stop immediate navigation
    const url = target.href;

    chrome.runtime.sendMessage({ type: "CHECK_PHISHING_URL", url }, (res) => {
      if (res.success) {
        if (res.data.phishing) {
          alert("⚠️ Red Zone: Phishing URL detected! Navigation blocked.");
        } else if (res.data.score > 0.3) {
          alert("⚠️ Yellow Zone: Possible phishing URL. Proceed with caution.");
          window.open(url, "_blank");
        } else {
          window.open(url, "_blank");
        }
      } else {
        window.open(url, "_blank");
      }
    });
  }

  // If an image (for upload)
  if (target.tagName === "IMG") {
    const imgUrl = target.src;

    fetch(imgUrl)
      .then((res) => res.blob())
      .then((blob) => {
        chrome.runtime.sendMessage({ type: "CHECK_PHISHING_IMAGE", file: blob }, (res) => {
          if (res.success) {
            if (res.data.phishing) {
              alert("⚠️ Red Zone: Phishing Image detected! Blocking access.");
            } else if (res.data.score > 0.3) {
              alert("⚠️ Yellow Zone: Possible phishing image.");
            } else {
              console.log("Image safe.");
            }
          }
        });
      });
  }
});
