export function screen_size() {

    let screenWidth = window.innerWidth;
    let screenHeight = window.innerHeight;

    alert(`Screen size is: ${screenWidth} x ${screenHeight}`);
    return [screenWidth, screenHeight];
}

