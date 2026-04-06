import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const requestData = [
  { date: 'Jan', requests: 320 },
  { date: 'Feb', requests: 280 },
  { date: 'Mar', requests: 350 },
  { date: 'Apr', requests: 400 },
  { date: 'May', requests: 370 },
  { date: 'Jun', requests: 420 },
  { date: 'Jul', requests: 390 },
  { date: 'Aug', requests: 410 },
  { date: 'Sep', requests: 380 },
  { date: 'Oct', requests: 430 },
  { date: 'Nov', requests: 440 },
  { date: 'Dec', requests: 460 },
];

export default function RequestsBarChart() {
  return (
    <div style={{ width: '100%' }}>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={requestData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" label={{ value: 'Date', position: 'insideBottomRight', offset: -5 }} />
          <YAxis label={{ value: 'Requests', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Bar dataKey="requests" fill="#8884d8" radius={[6, 6, 0, 0]} barSize={16} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
