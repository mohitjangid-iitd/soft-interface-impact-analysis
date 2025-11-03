# Impact and Deformation at Soft Interfaces

Experimental analysis of droplet impact and deformation dynamics on soft hydrogel surfaces.  
This repository contains Python scripts developed for data extraction, video analysis, and visualization used during my M.Sc. Physics thesis at **IIT Delhi**.

---

## 🧪 Overview
The project combines high-speed video analysis, data processing, and visualization to study how droplets deform soft surfaces upon impact.  
All experimental data and videos are excluded for confidentiality — only analysis scripts are included here.

---

## 📚 Academic Context
This work was carried out as part of the **M.Sc. Physics Thesis** at the  
**Indian Institute of Technology Delhi (IIT Delhi)**  
under the supervision of **Prof. Deepak Kumar**,  
Department of Physics, IIT Delhi.

---

## 📂 Code Structure
code/
├── video_analysis/
│ ├── converters/ → Convert videos (MP4 → AVI)
│ ├── droplet_detection/ → Track droplets, measure parameters, export CSVs
│ └── comparison/ → Compare processed videos
│
├── data_analysis/ → Plot, fit, and visualize extracted data
│
└── utils/ → Common helper functions

---

## ⚙️ Key Scripts

| File | Description |
|------|--------------|
| `mini_realtime_counter.py` | Basic prototype for droplet tracking using contour detection |
| `realtime_counter.py` | Advanced version with detailed measurement and deformation tracking |
| `measure_and_count_batch.py` | Batch analysis of multiple droplet videos |
| `ellipse_fit_single.py` | Ellipse fitting for shape estimation |
| `jet_length_vs_time.py` | Plots jet length variation over time |
| `volume_vs_flowrate.py` | Plots droplet volume vs flow rate |
| `functions.py` | Shared helper functions (used by multiple scripts) |

A complete description of all scripts is available in **`script_descriptions.txt`**.

---

## 🧰 Tools Used
- Python (OpenCV, NumPy, Pandas, Matplotlib, SciPy, scikit-image)
- Excel / Google Sheets for data logging
- ffmpeg for video frame conversion

---

## 🧑‍🔬 Author
**Mohit Jangid**  
M.Sc. Physics, IIT Delhi  
[GitHub](https://github.com/mohitjangid-iitd) | [LinkedIn](https://www.linkedin.com/in/mohitjangid-iitd)

**Supervisor:** Prof. Deepak Kumar  
Department of Physics, IIT Delhi

---

## 📜 Notes
This repository does **not** include experimental data or raw videos for confidentiality reasons.  
Example CSVs or demo datasets may be added later for illustration.

---
