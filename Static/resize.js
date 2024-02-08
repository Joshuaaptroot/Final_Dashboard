const resizableDiv = document.getElementById('resizableDiv');
let isResizing = false;
let isDragging = false;
let startX;
let startY;
const aspectRatio = resizableDiv.clientWidth / resizableDiv.clientHeight;

resizableDiv.addEventListener('mousedown', (event) => {
  if (event.target.classList.contains('chart-element')) {
    isDragging = true;
    startX = event.clientX - resizableDiv.offsetLeft;
    startY = event.clientY - resizableDiv.offsetTop;
    resizableDiv.style.cursor = 'grabbing';
  } else {
    isResizing = true;
    startX = event.clientX - resizableDiv.offsetWidth;
    startY = event.clientY - resizableDiv.offsetHeight;
    resizableDiv.style.cursor = 'grabbing';
  }

  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', () => {
    isResizing = false;
    isDragging = false;
    resizableDiv.style.cursor = 'grab';
    document.removeEventListener('mousemove', handleMouseMove);
  });
});

function handleMouseMove(event) {
  if (isResizing) {
    let newWidth = event.clientX - startX;
    let newHeight = newWidth / aspectRatio;

    // Check for minimum size
    newWidth = Math.max(newWidth, 200);

    // Ensure height is not greater than width
    newHeight = Math.min(newHeight, newWidth);

    resizableDiv.style.width = newWidth + 'px';
    resizableDiv.style.height = newHeight + 'px';
  } else if (isDragging) {
    const newLeft = event.clientX - startX;
    const newTop = event.clientY - startY;

    resizableDiv.style.left = newLeft + 'px';
    resizableDiv.style.top = newTop + 'px';
  }
}
