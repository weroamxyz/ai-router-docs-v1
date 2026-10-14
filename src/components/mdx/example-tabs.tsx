import type { ComponentProps } from 'react';
import { Tab, Tabs } from 'fumadocs-ui/components/tabs';

export function ExampleTabs(props: ComponentProps<typeof Tabs>) {
  return <Tabs updateAnchor {...props} />;
}

export function ExampleTab(props: ComponentProps<typeof Tab>) {
  return <Tab {...props} />;
}
