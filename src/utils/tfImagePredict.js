// src/utils/tfImagePredict.js
import * as tf from "@tensorflow/tfjs";

let imageModel = null;

export async function loadImageModelIfNeeded(modelUrl = "/models/image_phish/model.json") {
  if (!imageModel) {
    imageModel = await tf.loadLayersModel(modelUrl);
  }
  return imageModel;
}

// imageElement is an HTMLImageElement (or canvas)
export async function predictImageLocal(imageElement, modelUrl) {
  const model = await loadImageModelIfNeeded(modelUrl);
  const tensor = tf.browser.fromPixels(imageElement)
    .resizeNearestNeighbor([224, 224]) // depends on model
    .toFloat()
    .div(255.0)
    .expandDims(0);
  const out = model.predict(tensor);
  const scoreArr = await out.data();
  return scoreArr[0]; // 0..1 (higher = phishing)
}
