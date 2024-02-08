function createImage() {
    const chartContainer = document.getElementById('resizableDiv');
  
    html2canvas(chartContainer).then((canvas) => {
      const image = canvas.toDataURL('image/png');
      const imgElement = document.createElement('img');
      imgElement.src = image;
  
      // Append the image to the body or any other container
      document.body.appendChild(imgElement);
    });
  }
  