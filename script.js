async function loadDashboard(){
  const res=await fetch('/api/dashboard'); const data=await res.json();
  signalCount.textContent=data.stats.signals;
  vehicleCount.textContent=data.stats.vehicles;
  incidentCount.textContent=data.stats.incidents;
  violationCount.textContent=data.stats.violations;

  signalsGrid.innerHTML=data.signals.map(s=>`
    <div class="signal" onclick="toggleSignal(${s.id})">
      <div class="top"><div class="lights">
        <span class="light ${s.status==='RED'?'active':''}"></span>
        <span class="light ${s.status==='YELLOW'?'active':''}"></span>
        <span class="light ${s.status==='GREEN'?'active':''}"></span>
      </div><span class="badge ${s.status}">${s.status}</span></div>
      <h3>${s.location}</h3><p>${s.vehicles} vehicles detected</p>
    </div>`).join('');

  incidentList.innerHTML=data.incidents.length ? data.incidents.map(i=>`
    <div class="item"><b>${i.type}</b> — ${i.location}<br><span class="muted">${i.description||'No description'} • ${i.created_at}</span></div>`).join('') : '<p>No incidents reported yet.</p>';

  violationList.innerHTML=data.violations.length ? data.violations.map(v=>`
    <div class="item"><b>${v.vehicle_no}</b> — ${v.violation}<br><span class="muted">Fine ₹${v.fine} • ${v.created_at}</span></div>`).join('') : '<p>No violations added yet.</p>';
}
async function toggleSignal(id){await fetch(`/api/signals/${id}/toggle`,{method:'POST'});loadDashboard();}
async function submitForm(form,url){
  const data=Object.fromEntries(new FormData(form));
  const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  const j=await r.json(); alert(j.message||j.error); if(r.ok){form.reset();loadDashboard();}
}
document.getElementById('incidentForm').addEventListener('submit',e=>{e.preventDefault();submitForm(e.target,'/api/incidents')});
document.getElementById('violationForm').addEventListener('submit',e=>{e.preventDefault();submitForm(e.target,'/api/violations')});
loadDashboard();
setInterval(loadDashboard,30000);
