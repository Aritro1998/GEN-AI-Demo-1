import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { epoch: 1, accuracy: 0.62 },
  { epoch: 2, accuracy: 0.68 },
  { epoch: 3, accuracy: 0.74 },
  { epoch: 4, accuracy: 0.70 },
  { epoch: 5, accuracy: 0.77 },
  { epoch: 6, accuracy: 0.81 },
  { epoch: 7, accuracy: 0.79 },
  { epoch: 8, accuracy: 0.85 },
  { epoch: 9, accuracy: 0.80 },
  { epoch: 10, accuracy: 0.88 },
  { epoch: 11, accuracy: 0.83 },
  { epoch: 12, accuracy: 0.90 },
  { epoch: 13, accuracy: 0.87 },
  { epoch: 14, accuracy: 0.93 },
];

export default function AccuracyLineChart() {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 10 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="epoch" label={{ value: 'Epoch', position: 'insideBottomRight', offset: -5 }} />
        <YAxis domain={[0, 1]} tickFormatter={v => `${(v * 100).toFixed(0)}%`} label={{ value: 'Accuracy', angle: -90, position: 'insideLeft' }} />
        {/* <Tooltip formatter={v => `${(v * 100).toFixed(2)}%`} /> */}
        <Line type="monotone" dataKey="accuracy" stroke="#8884d8" strokeWidth={3} dot={{ r: 5 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}
