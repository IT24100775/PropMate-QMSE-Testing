import http from 'k6/http';
import { check } from 'k6';

const targetUrl =
  __ENV.TARGET_URL || 'http://127.0.0.1:5235/api/properties';

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '30s', target: 25 },
    { duration: '30s', target: 50 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.01'],
    checks: ['rate>0.99'],
  },
};

export default function () {
  const response = http.get(targetUrl);
  const isSuccessfulResponse =
    response.status === 200 &&
    (response.headers['Content-Type']?.includes('application/json') ?? false);

  if (!isSuccessfulResponse) {
    const bodyExcerpt = response.body.slice(0, 300).replace(/\s+/g, ' ');
    console.error(
      `Failed properties response: vu=${__VU} iteration=${__ITER} ` +
        `status=${response.status} ` +
        `contentType=${response.headers['Content-Type'] || 'missing'} ` +
        `body=${bodyExcerpt}`,
    );
  }

  check(response, {
    'properties API returns HTTP 200': (result) => result.status === 200,
    'properties API returns JSON': (result) =>
      result.headers['Content-Type']?.includes('application/json') ?? false,
  });
}
