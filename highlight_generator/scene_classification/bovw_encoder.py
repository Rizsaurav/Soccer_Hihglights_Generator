import os
import cv2
import numpy as np
from sklearn.cluster import KMeans
from scene_classification.brief_extractor import extract_brief_descriptors

def build_bovw_dictionary(frame_dir, n_clusters=100):
    all_descriptors = []

    for fname in sorted(os.listdir(frame_dir)):
        if fname.endswith(".jpg"):
            img_path = os.path.join(frame_dir, fname)
            img = cv2.imread(img_path)

            descs = extract_brief_descriptors(img)
            if descs.size > 0:
                all_descriptors.append(descs)

    # Stack into one big array
    all_descriptors = np.vstack(all_descriptors)
    print(f"[INFO] Clustering {all_descriptors.shape[0]} descriptors...")

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(all_descriptors)

    return kmeans

def encode_frame(image, kmeans_model):
    descs = extract_brief_descriptors(image)
    if descs.size == 0:
        return np.zeros(kmeans_model.n_clusters)

    labels = kmeans_model.predict(descs)
    hist = np.bincount(labels, minlength=kmeans_model.n_clusters)
    return hist / np.sum(hist)  # Normalize
