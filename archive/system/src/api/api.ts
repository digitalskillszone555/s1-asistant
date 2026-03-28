export async function getSystemLogs(): Promise<any[]> {
  console.log("Mock getSystemLogs called");
  return Promise.resolve([
    { timestamp: new Date().toISOString(), level: "INFO", message: "Application started successfully." },
    { timestamp: new Date(Date.now() - 60000).toISOString(), level: "WARN", message: "Low disk space warning on /dev/sda1." },
  ]);
}

export async function getNotifications(): Promise<any[]> {
  console.log("Mock getNotifications called");
  return Promise.resolve([
    { id: 1, type: "info", message: "New software update available.", read: false },
    { id: 2, type: "alert", message: "Critical security patch required.", read: false },
    { id: 3, type: "info", message: "Your subscription will expire soon.", read: true },
  ]);
}

export async function getSystemHealth(): Promise<{ cpu: number; memory: number; status: string }> {
  console.log("Mock getSystemHealth called");
  return Promise.resolve({
    cpu: Math.floor(Math.random() * 100),
    memory: Math.floor(Math.random() * 100),
    status: "healthy",
  });
}
