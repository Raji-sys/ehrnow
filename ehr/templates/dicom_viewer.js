// dicom-viewer.js
{% for study in radiology_files %}
const radiologyId = '{{ study.id }}';
const dicomUrl = `/dicom/${radiologyId}/`;

fetch(dicomUrl)
  .then(response => response.blob())
  .then(blob => {
    const file = new File([blob], 'dicom-file');
    const viewer = dicomWebViewer.createViewport();
    dicomWebViewer.loadFile(file).then(data => {
      viewer.setData(data);
      viewer.render(document.getElementById(`dicom-viewer-${radiologyId}`));
    });
  })
  .catch(error => {
    console.error('Error loading DICOM file:', error);
  });
{% endfor %}