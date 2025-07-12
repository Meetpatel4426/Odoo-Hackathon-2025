document.addEventListener("DOMContentLoaded", () => {
  const skillsOffered = ["Guitar", "Spanish", "Photoshop"];
  const skillsWanted = ["Coding", "Cooking"];

  const offeredContainer = document.getElementById("skillsOffered");
  const wantedContainer = document.getElementById("skillsWanted");

  skillsOffered.forEach(skill => {
    const tag = document.createElement("span");
    tag.textContent = skill;
    offeredContainer.appendChild(tag);
  });

  skillsWanted.forEach(skill => {
    const tag = document.createElement("span");
    tag.textContent = skill;
    wantedContainer.appendChild(tag);
  });
});

function openModal() {
  document.getElementById("modal").style.display = "flex";
}

function closeModal() {
  document.getElementById("modal").style.display = "none";
}

function submitRequest() {
  const yourSkill = document.getElementById("yourSkill").value;
  const wantedSkill = document.getElementById("wantedSkill").value;
  const message = document.getElementById("message").value;

  alert(`Swap request submitted:\nYour Skill: ${yourSkill}\nTheir Skill: ${wantedSkill}\nMessage: ${message}`);
  closeModal();
}
