function DetectionTable() {

  const detections = [
    { id: 1, class: "Person", confidence: 0.95 },
    { id: 2, class: "Bottle", confidence: 0.88 },
    { id: 3, class: "Chair", confidence: 0.91 }
  ];

  return (
    <div className="table-container">

      <h3>Detections</h3>

      <table>

        <thead>
          <tr>
            <th>ID</th>
            <th>Class</th>
            <th>Confidence</th>
          </tr>
        </thead>

        <tbody>
          {detections.map((item) => (
            <tr key={item.id}>
              <td>{item.id}</td>
              <td>{item.class}</td>
              <td>{item.confidence}</td>
            </tr>
          ))}
        </tbody>

      </table>

    </div>
  );
}

export default DetectionTable;