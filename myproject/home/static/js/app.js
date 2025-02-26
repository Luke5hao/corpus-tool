function updateWordCount() {
    var entry = document.getElementById('textBox').value;
    var words = entry.match(/\b[-?(\w+)?]+\b/gi);
    var numWords = words ? words.length : 0;
    var minWords = 200;

    document.getElementById('wordCount').innerText = 'Word count (minimum 200 words): ' + numWords;

    if(numWords < minWords){
        submitButton.preventDefault(); 
    }
}