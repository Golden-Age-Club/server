const { translate } = require('@vitalets/google-translate-api');

exports.translateText = async (req, res) => {
  const { text, targetLang } = req.body;
  try {
    if (!text || !targetLang) {
      return res.status(400).json({ error: 'Text and targetLang are required' });
    }

    // Map common language codes to Google Translate codes
    let lang = targetLang;
    const langMap = {
      'zh': 'zh-CN',
      'fil': 'tl', // Tagalog
      'id': 'id', // Indonesian
      'ms': 'ms', // Malay
      'th': 'th', // Thai
      'vi': 'vi', // Vietnamese
      'ar': 'ar', // Arabic
      'ja': 'ja', // Japanese
      'ko': 'ko', // Korean
    };
    
    if (langMap[targetLang]) {
        lang = langMap[targetLang];
    }

    // @vitalets/google-translate-api returns an object { text: '...' }
    const result = await translate(text, { to: lang });
    
    res.json({ 
      original: text, 
      translated: result.text,
      lang: lang
    });
  } catch (error) {
    console.error('Translation error:', error);
    // Fallback to original text if translation fails
    res.json({ original: text || '', translated: text || '', error: 'Translation failed' });
  }
};
