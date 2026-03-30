const fs = require('fs');
const path = require('path');

// 1. Find all items in the current directory
const items = fs.readdirSync(__dirname);

// 2. Filter out to only get project folders (ignore node_modules and hidden files)
const folders = items.filter(item => {
    const itemPath = path.join(__dirname, item);
    return fs.lstatSync(itemPath).isDirectory() && !item.startsWith('.') && item !== 'node_modules';
});

console.log(`Found ${folders.length} project folders. Compiling testing JSONs...\n`);

// Array to hold all the bug objects from all testing files across all repos
let allBugs = [];

// The files we want to extract from each folder
const targetFiles = ['testing_1.json', 'testing_2.json', 'testing_3.json'];

// 3. Loop through every folder
folders.forEach(folder => {
    let folderBugCount = 0;

    targetFiles.forEach(filename => {
        const jsonPath = path.join(__dirname, folder, filename);
        
        // Check if the file actually exists before reading it
        if (fs.existsSync(jsonPath)) {
            try {
                // Read and parse the JSON file
                const rawData = fs.readFileSync(jsonPath, 'utf8');
                const parsedData = JSON.parse(rawData);
                
                // If the file is an array of bugs, concatenate it to our master array
                if (Array.isArray(parsedData)) {
                    allBugs = allBugs.concat(parsedData);
                    folderBugCount += parsedData.length;
                } else {
                    // Fallback just in case it's a single object instead of an array
                    allBugs.push(parsedData);
                    folderBugCount += 1;
                }
            } catch (error) {
                console.error(`  [X] Error reading or parsing ${folder}/${filename}: ${error.message}`);
            }
        }
    });

    if (folderBugCount > 0) {
        console.log(`  ✓ Extracted ${folderBugCount} bugs from ${folder}`);
    } else {
        console.log(`  ! No testing JSONs found in ${folder}`);
    }
});

// 4. Write everything to a single demo.json file in the root directory
const outputPath = path.join(__dirname, 'demo.json');
fs.writeFileSync(outputPath, JSON.stringify(allBugs, null, 4), 'utf8');

console.log(`\n🎉 Successfully compiled ${allBugs.length} total bugs into demo.json!`);
console.log(`📁 File saved at: ${outputPath}`);