// src/utils/tfModel.js
import * as tf from "@tensorflow/tfjs";

let model = null;
let modelLoadPromise = null;

/**
 * Load the TFJS model from public/models/phishing_model/model.json
 * Put your converted model there (use tensorflowjs_converter or Kaggle flow)
 */
export function loadPhishModel() {
  if (model) return Promise.resolve(model);
  if (modelLoadPromise) return modelLoadPromise;
  modelLoadPromise = tf.loadLayersModel("/models/phishing_model/model.json")
    .then((m) => {
      model = m;
      console.log("TFJS model loaded:", model);
      return model;
    })
    .catch((err) => {
      console.warn("Failed to load TFJS model:", err);
      modelLoadPromise = null;
      throw err;
    });
  return modelLoadPromise;
}

/**
 * Predict from numeric feature array (length 10 as per featureHelpers)
 * returns array of probabilities [url_score, image_score, file_score] or null on error
 */
export async function predictFromFeatures(featuresArray) {
  try {
    if (!featuresArray || !Array.isArray(featuresArray)) return null;
    const m = await loadPhishModel();
    if (!m) return null;
    const tfInput = tf.tensor2d([featuresArray], [1, featuresArray.length], "float32");
    const out = m.predict(tfInput);
    const data = await out.data();
    tfInput.dispose();
    if (Array.from) return Array.from(data);
    return data;
  } catch (e) {
    console.warn("predictFromFeatures error:", e);
    return null;
  }
}
