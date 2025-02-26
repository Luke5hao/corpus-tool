function updateWordCount() {
    var text = document.getElementById('textBox').value;
    var words = text.match(/\b[-?(\w+)?]+\b/gi);
    var count = words ? words.length : 0;
    document.getElementById('wordCount').innerText = 'Word count: ' + count;
}