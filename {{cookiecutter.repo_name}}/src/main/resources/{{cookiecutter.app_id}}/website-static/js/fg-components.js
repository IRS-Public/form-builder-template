// This application's flow entry point.
//
// The custom elements, the Fact Graph bootstrap and the navigation all come from taxpert's
// flow-runtime bundle — importing it is what defines <fg-set>, <fg-collection>, <fg-show> and the
// rest. The scaffold's page template loads this file, not the bundle directly, so that an app has
// somewhere to add its own client-side behaviour.
//
// Add yours below the import: a custom element registered as a `nodeTypes` entry on the
// FormativeApp, a knockout gate, a confirmation before a destructive change. Order matters only in
// that the runtime must come first — it owns the Fact Graph anything else reads at import time.

import '../vendor/taxpert/flow-runtime/js/flow-runtime.js'
