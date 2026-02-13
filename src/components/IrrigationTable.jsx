import React from 'react';
import '../styles/IrrigationTable.css';

function IrrigationTable({ rows }) {
  return (
    <div className="irrigation-table card">
      <h3>Next 7 Days Irrigation Plan</h3>
      <div className="table">
        <div className="table-header">
          <span>Date</span>
          <span>Stage</span>
          <span>Planned Water</span>
          <span>Weather Adj</span>
          <span>Status</span>
        </div>
        {rows.length === 0 && (
          <div className="table-row empty">No irrigation events scheduled.</div>
        )}
        {rows.map((row) => (
          <div key={row.date} className="table-row">
            <span>{row.date}</span>
            <span>{row.stage}</span>
            <span>{row.plannedWater}</span>
            <span>{row.weatherAdjustment}</span>
            <span className={`status-pill ${row.status.toLowerCase()}`}>{row.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default IrrigationTable;
