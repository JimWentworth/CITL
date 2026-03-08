const fs = require('fs');
const path = require('path');

// Function to add a stylesheet link to an HTML file
function addStylesheetLinkToFile(filePath, stylesheetLink) {
    fs.readFile(filePath, 'utf8', (err, data) => {
        if (err) {
            console.error('Error reading the file:', err);
            return;
        }
        // Check if the link already exists
        if (data.includes(stylesheetLink)) {
            console.log('Stylesheet link already exists in', filePath);
            return;
        }
        // Insert the link before the closing head tag
        const newContent = data.replace(/<\/head>/, `    <link rel="stylesheet" href="${stylesheetLink}">
    <\/head>`);
        fs.writeFile(filePath, newContent, 'utf8', (err) => {
            if (err) {
                console.error('Error writing to the file:', err);
            } else {
                console.log('Stylesheet link added to', filePath);
            }
        });
    });
}

// Directory containing HTML files
const directoryPath = path.join(__dirname, 'ai-fluency');
const stylesheetLink = 'path/to/your/stylesheet.css'; // Modify this line with your actual stylesheet path

// Read all HTML files in the directory
fs.readdir(directoryPath, (err, files) => {
    if (err) {
        console.error('Error reading the directory:', err);
        return;
    }
    files.forEach(file => {
        if (path.extname(file) === '.html') {
            addStylesheetLinkToFile(path.join(directoryPath, file), stylesheetLink);
        }
    });
});
