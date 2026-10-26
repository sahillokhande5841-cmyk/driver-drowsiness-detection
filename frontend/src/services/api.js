import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

const client = axios.create({
  baseURL: API_BASE,
  timeout: 5000,
});

export const getHealth = async () => {
  const res = await client.get("/api/health");
  return res.data;
};

export const getStatus = async () => {
  const res = await client.get("/status");
  return res.data;
};

export const startDetector = async () => {
  const res = await client.post("/start");
  return res.data;
};

export const stopDetector = async () => {
  const res = await client.post("/stop");
  return res.data;
};

export const recalibrate = async () => {
  const res = await client.post("/recalibrate");
  return res.data;
};

export const setSettings = async (settings) => {
  const res = await client.post("/settings", settings);
  return res.data;
};

export const triggerTestAlert = async (type = "DROWSINESS") => {
  const res = await client.post("/alert/test", null, { params: { type } });
  return res.data;
};

export default client;
