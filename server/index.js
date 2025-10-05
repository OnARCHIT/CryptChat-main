// server/index.js
import express from 'express';
import fetch from 'node-fetch';
import cors from 'cors';
import 'dotenv/config';

const app = express();
app.use(cors()); // allow cross-origin requests from frontend
app.use(express.json());

const PORT = process.env.PORT || 3001;

app.post('/api/news', async (req, res) => {
  const { q = 'phishing OR "phishing attack" OR "data breach" OR deepfake' } = req.body;
  const NEWS_API_KEY = process.env.NEWS_API_KEY;

  if (!NEWS_API_KEY) {
    return res.status(500).json({ error: 'Missing NEWS_API_KEY in environment variables' });
  }

  const url = `https://newsapi.org/v2/everything?q=${encodeURIComponent(q)}&pageSize=8&sortBy=publishedAt&language=en`;

  try {
    const response = await fetch(url, { headers: { 'X-Api-Key': NEWS_API_KEY } });
    const data = await response.json();

    if (data.status !== 'ok') {
      return res.status(500).json({ error: data.message || 'NewsAPI error' });
    }

    // Return only essential fields for frontend
    const articles = data.articles?.map(a => ({
      title: a.title,
      description: a.description,
      url: a.url,
      urlToImage: a.urlToImage,
      publishedAt: a.publishedAt,
      source: a.source.name
    })) || [];

    res.json({ articles });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => console.log(`News proxy listening on port ${PORT}`));
