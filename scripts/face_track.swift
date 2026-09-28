import Foundation
import Vision
import AppKit
// usage: face <dir> <step>   -> prints "file cx cy w h" normalized (top-left origin)
let args = CommandLine.arguments
let dir = args[1]; let step = Int(args[2]) ?? 30
let fm = FileManager.default
let files = (try? fm.contentsOfDirectory(atPath: dir))?.filter { $0.hasSuffix(".jpg") }.sorted() ?? []
var i = 0
for f in files {
  if i % step != 0 { i += 1; continue }
  i += 1
  guard let img = NSImage(contentsOfFile: dir + "/" + f), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
  let req = VNDetectFaceRectanglesRequest()
  try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
  if let r = (req.results ?? []).max(by: { $0.boundingBox.width < $1.boundingBox.width }) {
    let b = r.boundingBox
    print(String(format: "%@ %.4f %.4f %.4f %.4f", f, b.midX, 1 - b.midY, b.width, b.height))
  } else { print("\(f) none") }
}
