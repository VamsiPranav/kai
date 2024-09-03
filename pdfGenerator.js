// File: pdfGenerator.js

window.generateAndDownloadPDF = async function(jsonData) {
  const regularFontUrl = 'fonts/GeneralSans-Regular.ttf';
  const boldFontUrl = 'fonts/GeneralSans-SemiBold.ttf';

  const regularFont = await fetch(regularFontUrl).then(res => res.arrayBuffer());
  const boldFont = await fetch(boldFontUrl).then(res => res.arrayBuffer());

  const pdf = new window.jspdf.jsPDF();

  pdf.addFont(regularFontUrl, "GeneralSans", "normal");
  pdf.addFont(boldFontUrl, "GeneralSans", "bold");

  pdf.setFont("GeneralSans");

  const lineHeight = 7;
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 10;
  let yOffset = margin;

  function addNewPage() {
    pdf.addPage();
    yOffset = margin;
  }

  function checkForNewPage(height) {
    if (yOffset + height > pageHeight - margin) {
      addNewPage();
    }
  }

  pdf.setFontSize(16);
  pdf.setFont("GeneralSans", "bold");
  pdf.text('Insights Report', pageWidth / 2, yOffset, { align: 'center' });
  yOffset += lineHeight * 2;

  pdf.setFontSize(12);
  for (let key in jsonData) {
    checkForNewPage(lineHeight * 2);

    pdf.setFont("GeneralSans", "bold");
    pdf.text(`${key}:`, margin, yOffset);

    pdf.setFont("GeneralSans", "normal");
    const value = jsonData[key].toString();
    const splitValue = pdf.splitTextToSize(value, pageWidth - margin * 2 - 30); // 30 is approx width of key

    checkForNewPage(lineHeight * splitValue.length);
    pdf.text(splitValue, margin + 30, yOffset);
    yOffset += lineHeight * Math.max(splitValue.length, 1);

    yOffset += lineHeight / 2;
  }

  pdf.save('report.pdf');
};