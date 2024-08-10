export function screen_size() {

    let screenWidth = window.innerWidth;
    let screenHeight = window.innerHeight;

    alert(`Screen size is: ${screenWidth} x ${screenHeight}`);

}

export function sendCustomEvent() {
	alert("Sending");
	const ev = new CustomEvent("myinfo", {
		detail: {
			payload: window.screen.height,
			callback: () => {
				alert("Custom event sent successfully.");
			},
		},
	});
	globalThis.core.forwardEvent(ev, [{componentId: "root", instanceNumber: 0}], true);
}