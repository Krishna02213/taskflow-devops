import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "20s", target: 30 },
    { duration: "60s", target: 100 },
    { duration: "20s", target: 0 },
  ],
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<500"],
  },
};

const baseUrl =
  __ENV.BASE_URL || "http://host.docker.internal:8002";

export default function () {
  const response = http.get(`${baseUrl}/health`);

  check(response, {
    "health returned 200": (result) => result.status === 200,
  });

  sleep(0.05);
}