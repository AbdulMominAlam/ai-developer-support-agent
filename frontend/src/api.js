import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    Authorization: "Bearer fda40cf7ace9ab49144708d3e4720be062fa92d0f26f1850064f7420678bd047",
  },
});

export default api;