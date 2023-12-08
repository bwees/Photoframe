
#include <FS.h>
#include <LittleFS.h>

void listFiles(void) {
  Serial.println();
  Serial.println("LittleFS files found:");

  fs::Dir dir = LittleFS.openDir(""); // Root directory
  String  line = "=====================================";
  uint32_t totalBytes = 0;

  Serial.println(line);
  Serial.println("  File name               Size");
  Serial.println(line);

  while (dir.next()) {
    String fileName = dir.fileName();
    Serial.print(fileName);
    int spaces = 25 - fileName.length(); // Tabulate nicely
    while (spaces--) Serial.print(" ");
    fs::File f = dir.openFile("r");
    Serial.print(f.size()); Serial.println(" bytes");
    totalBytes += f.size();
  }
  Serial.println(); Serial.print("Total = ");
  int spaces = 25 - 8; // Tabulate nicely
  while (spaces--) Serial.print(" ");
  Serial.print(totalBytes); Serial.println(" bytes");

  Serial.println(line);
  Serial.println();
  delay(1000);
}

