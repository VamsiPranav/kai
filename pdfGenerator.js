// File: pdfGenerator.js

window.generateAndDownloadPDF = async function(jsonData) {

  const pdf = new window.jspdf.jsPDF();

  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  let yOffset = 10

  pdf.setFont("GeneralSans", "bold");
  pdf.setFontSize(16);

  pdf.text('Insights Report', pageWidth / 2, yOffset, { align: 'center' });
  yOffset += 10;

  pdf.setFontSize(12);
  pdf.setFont("GeneralSans", "normal");
  for (let key in jsonData) {

    const value = jsonData[key].toString();
    const lines = pdf.splitTextToSize(value, 180); 

    lines.forEach(line => {
      // Check if the next line will exceed the page height
      if (yOffset + 7 > pageHeight) { // 10 is the height of each line in mm
        pdf.addPage(); // Add a new page
        yOffset = 10; // Reset vertical position for the new page
      }
      pdf.text(line, 20, yOffset); // Add text to PDF
      yOffset += 7; // Move down for the next line
    });
  }

  pdf.save('report.pdf');
};