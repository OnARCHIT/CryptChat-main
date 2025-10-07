const status = document.getElementById("status");
const checkNow = document.getElementById("checkNow");

checkNow.addEventListener("click", async () => {
  status.textContent = "Checking current tab...";
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => alert("CryptChat is active and monitoring links/images!")
  });
  status.textContent = "Monitoring active.";
});
