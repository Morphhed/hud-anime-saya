# Assetto Corsa Custom HUD


![ShiftLight Preview](preview.png)


---


## Fitur

* **Shift Light Dinamis**: Lampu RPM bakal berubah bertahap dari `green.png` & `green2.png` ➔ `yellow.png` & `yellow2.png` ➔ `red.png` (serta kedip-kedip selang-seling dengan `blank.png` pas RPM sudah mau mentok).

* **Mode Mesin Limit (Cooked Light)**: Keluar indikator `cooked.png` kalau kamu geber RPM kelewatan batas aman.

* **Efek Tabrakan Selang-Seling**: Begitu mobil nabrak keras, gambarnya bakal ganti-gantian antara `collision.png` dan `pog.png` tiap kali terjadi benturan baru.

* **Efek Getar Mesin (Engine Shake)**: Layar HUD bakal ikut bergetar pas mesin digeber di atas 4000 RPM biar makin dapet sensasinya.

* **Speedometer Digital**: Rata kanan rapi, dan bisa kamu ganti antara **KM/H** atau **MPH**.

* **Menu Pengaturan di Dalam Game**: Bisa bebas matiin/nyalain fitur lewat jendela *Settings* pas lagi di dalam trek.

---


## File & Aset 

```text

ShiftLight/

├── ShiftLight.py

├── sim\_info.py

├── third\_party/

├── stdlib/

├── stdlib64/

└── images/

&#x20;   ├── frame.png

&#x20;   ├── green.png / green2.png

&#x20;   ├── yellow.png / yellow2.png

&#x20;   ├── red.png / blank.png

&#x20;   ├── cooked.png

&#x20;   ├── collision.png

&#x20;   ├── pog.png

&#x20;   ├── speed\_digits/ (angka 0-9)

&#x20;   └── speed\_unit/ (kmh.png \& mph.png)

