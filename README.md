# ArtSearch
Harvard AC295 EX1

Working notes: https://docs.google.com/document/d/13XLbRWwB6qrgopuGRTRjrP_6O2y9ctloeIGEfz3qEKs/edit?ts=5f7362a1

```
git clone https://github.com/DesmondYuan/ArtSearch
cd ArtSearch
sudo docker build .
sudo docker run -d -p 8081:5000 echo_translate
curl http://34.94.24.130:8081/translate?msg='hello'&?language='en'
```