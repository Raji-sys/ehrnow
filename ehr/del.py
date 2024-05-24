<script src="{% static 'cornerstoneTools.min.js' %}"></script>
{% for study in radiology_studies %}
<script>
  const radiologyId = '{{ study.id }}';
  const dicomUrl = `/dicom/${radiologyId}/`;

  fetch(dicomUrl)
    .then(response => response.arrayBuffer())
    .then(buffer => {
      cornerstoneWebImageLoader.webWorkerDecodeConfig.initCodecsOnStartup = false;
      cornerstoneWADOImageLoader.webWorkerDecodeConfig.initCodecsOnStartup = false;
      cornerstone.registerImageLoader('dicomfile', cornerstoneWADOImageLoader.loadImage);
      const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(buffer);
      cornerstone.loadAndCacheImage(imageId).then(image => {
        const viewer = cornerstone.loadImage(imageId, {
          viewport: {
            element: document.getElementById(`dicom-viewer-${radiologyId}`),
          }
        });
        cornerstone.enable(viewer);
      });
    });
</script>
{% endfor %}