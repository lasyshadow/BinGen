const axios = require('axios');
const fs = require('fs');
const readline = require('readline');
const { Worker, isMainThread, parentPort } = require('worker_threads');
const ProgressBar = require('progress');

function generateBin(cardType, customPrefix = null) {
    if (customPrefix) return customPrefix;

    const randomDigits = (length) => Array.from({ length }, () => Math.floor(Math.random() * 10)).join('');

    switch (cardType) {
        case 'Visa':
            return '4' + randomDigits(5);
        case 'MasterCard':
            return String([51, 52, 53, 54, 55][Math.floor(Math.random() * 5)]) + randomDigits(4);
        case 'American Express':
            return String([34, 37][Math.floor(Math.random() * 2)]) + randomDigits(3);
        case 'Discover':
            return '6011' + randomDigits(2);
        case 'JCB':
            return '35' + randomDigits(4);
        case 'Diners Club':
            return String([300, 301, 302, 303, 304, 305][Math.floor(Math.random() * 6)]) + randomDigits(2);
        case 'UnionPay':
            return '62' + randomDigits(4);
        default:
            return null;
    }
}

async function checkBin(binNumber) {
    const url = `https://binlist.io/lookup/${binNumber}`;
    let retries = 3;

    while (retries > 0) {
        try {
            const response = await axios.get(url, { timeout: 5000 });
            if (response.status === 200) {
                const data = response.data;
                return {
                    bin: binNumber,
                    scheme: data.scheme || 'N/A',
                    country: data.country?.name || 'N/A',
                    type: data.type || 'N/A',
                    category: data.category || 'N/A',
                    bank: data.bank?.name || 'N/A'
                };
            }
        } catch (error) {
            retries -= 1;
            await new Promise(resolve => setTimeout(resolve, Math.random() * 2000 + 1000));
        }
    }
    return null;
}

async function generateBins(cardType, amount, customPrefix = null) {
    const validBins = [];
    const bar = new ProgressBar('Generating and checking BINs [:bar] :percent', { total: amount, width: 30 });

    const processBin = async () => {
        const binNum = generateBin(cardType, customPrefix);
        if (binNum) {
            const fullBin = binNum + Array.from({ length: 10 - binNum.length }, () => Math.floor(Math.random() * 10)).join('');
            const binData = await checkBin(fullBin);
            if (binData) validBins.push(binData);
        }
        bar.tick();
    };

    const tasks = Array.from({ length: amount }, processBin);
    await Promise.all(tasks);

    return validBins;
}

function prompt(question) {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    return new Promise((resolve) => rl.question(question, (answer) => { rl.close(); resolve(answer); }));
}

async function main() {
    console.log(`
=====================
    BIN GENERATOR
=====================
    DEV - @XDPRO2
    `);

    const cardType = await prompt('Enter card type (Visa, MasterCard, American Express, Discover, JCB, Diners Club, UnionPay): ').trim();
    let customPrefix = await prompt('Enter a custom BIN prefix (or leave empty): ').trim();
    customPrefix = customPrefix === '' ? null : customPrefix;
    const amount = parseInt(await prompt('Enter the number of BINs to generate: '), 10);

    const validBins = await generateBins(cardType, amount, customPrefix);

    if (validBins.length > 0) {
        const filename = `${cardType}-bins.txt`;
        fs.writeFileSync(filename, validBins.map(bin => JSON.stringify(bin)).join('\n'));
        console.log(`${validBins.length} valid BINs saved to ${filename}.`);
    } else {
        console.log('No valid BINs generated.');
    }
}

if (isMainThread) {
    main();
}
