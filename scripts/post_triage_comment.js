const fs = require('fs');

module.exports = async function (
  {github, context, core}, path = 'summary.md'
) {
  const pr = context.payload.pull_request;
  const labels = pr?.labels?.map(l => l.name) || [];
  if (!labels.includes('sqf:triage')) {
    core.info('sqf:triage label missing');
    return false;
  }
  let body = '';
  try {
    body = fs.readFileSync(path, 'utf8').trim();
  } catch {
    core.info(`missing ${path}`);
    return false;
  }
  if (!body) {
    core.info('empty summary');
    return false;
  }
  await github.rest.issues.createComment({
    issue_number: pr.number,
    owner: context.repo.owner,
    repo: context.repo.repo,
    body
  });
  return true;
};
