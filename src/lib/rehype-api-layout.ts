type HastNode = {
  children?: HastNode[];
  properties?: Record<string, unknown>;
  tagName?: string;
  type: string;
  [key: string]: unknown;
};

type HastRoot = HastNode & {
  children: HastNode[];
};

type VFileLike = {
  data?: {
    frontmatter?: Record<string, unknown>;
  };
};

function isElement(node: HastNode, tagName: string) {
  return node.type === 'element' && node.tagName === tagName;
}

function createSection(className: string, headingLevel: number): HastNode {
  return {
    type: 'element',
    tagName: 'section',
    properties: {
      className: [className],
      'data-heading-level': headingLevel,
    },
    children: [],
  };
}

function groupSubsections(children: HastNode[]) {
  const grouped: HastNode[] = [];
  let subsection: HastNode | undefined;

  for (const child of children) {
    if (isElement(child, 'h3')) {
      subsection = createSection('api-subsection', 3);
      subsection.children!.push(child);
      grouped.push(subsection);
      continue;
    }

    if (subsection) subsection.children!.push(child);
    else grouped.push(child);
  }

  return grouped;
}

/**
 * Adds semantic wrappers around heading-delimited API sections so nested
 * subsections can receive the inset rail without changing the authored MDX.
 * Field schemas and examples remain fully explicit in each document.
 */
export function rehypeApiLayout() {
  return (tree: HastRoot, file: VFileLike) => {
    if (file.data?.frontmatter?.sectionLayout !== 'api') return;

    const grouped: HastNode[] = [];
    let section: HastNode | undefined;

    for (const child of tree.children) {
      if (isElement(child, 'h2')) {
        section = createSection('api-section', 2);
        section.children!.push(child);
        grouped.push(section);
        continue;
      }

      if (section) section.children!.push(child);
      else grouped.push(child);
    }

    for (const child of grouped) {
      if (
        isElement(child, 'section') &&
        child.properties?.className instanceof Array &&
        child.properties.className.includes('api-section')
      ) {
        child.children = groupSubsections(child.children ?? []);
      }
    }

    tree.children = grouped;
  };
}
